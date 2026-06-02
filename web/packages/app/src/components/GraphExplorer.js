import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Graph } from 'react-d3-graph';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Popover,
  Typography,
} from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const NODE_COLORS = {
  AOP: '#F78888',
  AdverseOutcome: '#F3D250',
  Assay: '#8eacbb',
  Chemical: '#90CCF4',
  ChemicalList: '#b0bec5',
  Disease: '#ef9a9a',
  Gene: '#A16E83',
  KeyEvent: '#B19F9E',
  MolecularInitiatingEvent: '#CEBC81',
  Pathway: '#97AABD',
};

const REL_DISPLAY = {
  chemicalIncreasesExpression: 'increases expression of',
  chemicalDecreasesExpression: 'decreases expression of',
  chemicalHasActiveAssay: 'is active in assay',
  chemicalHasInactiveAssay: 'is inactive in assay',
  chemicalInList: 'is in list',
  geneInPathway: 'participates in',
  geneInteractsWithGene: 'interacts with',
  geneAssociatesWithDisease: 'associated with',
  PathwayContainsGene: 'contains gene',
  aopIncludesKE: 'includes key event',
  keIncludedInAOP: 'is included in AOP',
  keyEventTriggers: 'triggers',
  keyEventTriggeredBy: 'triggered by',
  listIncludesChemical: 'includes chemical',
};

const HOST = import.meta.env.PROD ? 'https://api.comptox.ai' : 'http://localhost:3001';

const graphConfig = {
  directed: false,
  nodeHighlightBehavior: true,
  linkHighlightBehavior: true,
  automaticRearrangeAfterDropNode: true,
  d3: {
    gravity: -300,
    linkLength: 140,
    alphaTarget: 0.05,
  },
  node: {
    labelProperty: 'label',
    fontSize: 10,
    size: 350,
    highlightStrokeColor: '#333',
    highlightFontSize: 11,
    highlightFontWeight: 'bold',
  },
  link: {
    highlightColor: '#333',
    renderLabel: true,
    labelProperty: 'label',
    fontSize: 8,
  },
};

function buildGraphData(nodes, edges) {
  const graphNodes = nodes.map((n) => ({
    id: String(n.nodeId),
    label: n.commonName || n.nodeFeatures?.[0]?.featValue || `ID: ${n.nodeId}`,
    color: NODE_COLORS[n.nodeType] || '#ccc',
    nodeType: n.nodeType,
    _raw: n,
  }));

  const nodeIdSet = new Set(graphNodes.map((n) => n.id));
  const graphLinks = edges
    .filter((e) => nodeIdSet.has(String(e.source)) && nodeIdSet.has(String(e.target)))
    .map((e) => ({
      source: String(e.source),
      target: String(e.target),
      label: REL_DISPLAY[e.relType] || e.relType,
    }));

  const seen = new Set();
  const dedupedLinks = graphLinks.filter((l) => {
    const key = [l.source, l.target, l.label].sort().join('::');
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  return { nodes: graphNodes, links: dedupedLinks };
}

export default function GraphExplorer({ seedNodes, seedEdges, onQueryFromNode }) {
  const [allNodes, setAllNodes] = useState([]);
  const [allEdges, setAllEdges] = useState([]);
  const [expandedIds, setExpandedIds] = useState(new Set());
  const [loading, setLoading] = useState(null);
  const [popover, setPopover] = useState(null);
  const [neighborCounts, setNeighborCounts] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!seedNodes?.length) return;
    setAllNodes(seedNodes);
    setAllEdges(seedEdges || []);
    setExpandedIds(new Set());
  }, [seedNodes, seedEdges]);

  const handleClickNode = useCallback(async (nodeId) => {
    if (expandedIds.has(nodeId)) return;

    try {
      const res = await fetch(`${HOST}/nodes/${nodeId}/neighborCounts`);
      const counts = await res.json();
      setNeighborCounts(counts);
      const clickedEl = containerRef.current?.querySelector(`g.node[id="${nodeId}"]`) || containerRef.current;
      setPopover({ nodeId, anchor: clickedEl });
    } catch {
      setNeighborCounts([]);
    }
  }, [expandedIds]);

  const handleExpand = useCallback(async (nodeId, relType) => {
    setPopover(null);
    setLoading(nodeId);

    try {
      const url = relType
        ? `${HOST}/nodes/${nodeId}/neighbors?relType=${relType}&limit=20`
        : `${HOST}/nodes/${nodeId}/neighbors?limit=20`;
      const res = await fetch(url);
      const data = await res.json();

      setAllNodes((prev) => {
        const existingIds = new Set(prev.map((n) => n.nodeId));
        const newNodes = (data.nodes || []).filter((n) => !existingIds.has(n.nodeId));
        return [...prev, ...newNodes];
      });

      setAllEdges((prev) => {
        const existingKeys = new Set(prev.map((e) => `${e.source}-${e.target}-${e.relType}`));
        const newEdges = (data.edges || []).filter(
          (e) => !existingKeys.has(`${e.source}-${e.target}-${e.relType}`)
        );
        return [...prev, ...newEdges];
      });

      setExpandedIds((prev) => new Set([...prev, nodeId]));
    } catch {
      // ignore
    }
    setLoading(null);
  }, []);

  const handleClosePopover = useCallback(() => {
    setPopover(null);
    setNeighborCounts([]);
  }, []);

  const handleQueryFromNode = useCallback((node) => {
    setPopover(null);
    if (onQueryFromNode) {
      onQueryFromNode(node);
    }
  }, [onQueryFromNode]);

  if (!allNodes.length) return null;

  const graphData = buildGraphData(allNodes, allEdges);
  if (!graphData.nodes.length) return null;

  const clickedNode = popover ? allNodes.find((n) => String(n.nodeId) === String(popover.nodeId)) : null;

  return (
    <Box ref={containerRef} sx={{ position: 'relative' }}>
      <Paper variant="outlined" sx={{ height: 400, overflow: 'hidden' }}>
        <Graph
          id={`graph-explorer-${seedNodes?.[0]?.nodeId || 'default'}`}
          data={graphData}
          config={{ ...graphConfig, width: 850, height: 400 }}
          onClickNode={handleClickNode}
        />
      </Paper>

      {loading && (
        <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
          <CircularProgress size={20} />
        </Box>
      )}

      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
        Click a node to expand its neighbors. {allNodes.length} nodes, {graphData.links.length} edges shown.
      </Typography>

      <Popover
        open={Boolean(popover)}
        anchorEl={popover?.anchor}
        onClose={handleClosePopover}
        anchorOrigin={{ vertical: 'center', horizontal: 'center' }}
        transformOrigin={{ vertical: 'center', horizontal: 'center' }}
      >
        {clickedNode && (
          <Box sx={{ p: 1.5, minWidth: 220, maxWidth: 320 }}>
            <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
              <Chip size="small" label={clickedNode.nodeType} sx={{ backgroundColor: NODE_COLORS[clickedNode.nodeType], fontWeight: 600, height: 20, fontSize: '0.7rem', mr: 0.5 }} />
              {clickedNode.commonName || 'Unnamed'}
            </Typography>
            <Divider sx={{ my: 0.5 }} />

            {neighborCounts.length > 0 ? (
              <>
                <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Expand neighbors:</Typography>
                <List dense disablePadding sx={{ maxHeight: 200, overflow: 'auto' }}>
                  {neighborCounts.map((nc) => (
                    <ListItemButton
                      key={`${nc.relType}-${nc.targetType}`}
                      onClick={() => handleExpand(popover.nodeId, nc.relType)}
                      sx={{ py: 0.25, borderRadius: 0.5 }}
                    >
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                            {REL_DISPLAY[nc.relType] || nc.relType}
                          </Typography>
                        }
                        secondary={`${nc.count} ${nc.targetType} nodes`}
                      />
                    </ListItemButton>
                  ))}
                </List>
              </>
            ) : (
              <Typography variant="caption" color="text.secondary">No neighbors found.</Typography>
            )}

            <Divider sx={{ my: 0.5 }} />
            {onQueryFromNode && (
              <Button
                size="small"
                startIcon={<OpenInNewIcon fontSize="small" />}
                onClick={() => handleQueryFromNode(clickedNode)}
                sx={{ textTransform: 'none', fontSize: '0.75rem' }}
              >
                Start new query from this node
              </Button>
            )}
          </Box>
        )}
      </Popover>
    </Box>
  );
}
