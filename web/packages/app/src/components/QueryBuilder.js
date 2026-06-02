import React, { useCallback, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Collapse,
  FormControl,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import CloseIcon from '@mui/icons-material/Close';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import SearchIcon from '@mui/icons-material/Search';

import {
  useFetchEdgeSchemaQuery,
  useExecutePatternMutation,
} from '../features/comptoxApiSlice';
import GraphExplorer from './GraphExplorer';

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

const NODE_FIELDS = {
  Chemical: [
    { field: 'commonName', label: 'Name' },
    { field: 'xrefCasRN', label: 'CAS RN' },
    { field: 'xrefDTXSID', label: 'DSSTOX ID' },
    { field: 'xrefPubchemCID', label: 'PubChem CID' },
    { field: 'synonyms', label: 'Synonyms' },
  ],
  Gene: [
    { field: 'geneSymbol', label: 'Gene Symbol' },
    { field: 'commonName', label: 'Name' },
    { field: 'xrefNcbiGene', label: 'NCBI Gene ID' },
    { field: 'xrefEnsembl', label: 'Ensembl ID' },
  ],
  Pathway: [
    { field: 'commonName', label: 'Name' },
    { field: 'pathwayId', label: 'Pathway ID' },
  ],
  AOP: [
    { field: 'commonName', label: 'Name' },
    { field: 'xrefAOPWikiAOPID', label: 'AOPWiki ID' },
  ],
  KeyEvent: [
    { field: 'keyEventName', label: 'Name' },
    { field: 'xrefAOPWikiKEID', label: 'AOPWiki KE ID' },
  ],
  AdverseOutcome: [
    { field: 'commonName', label: 'Name' },
    { field: 'xrefAOPWikiKEID', label: 'AOPWiki KE ID' },
  ],
  MolecularInitiatingEvent: [
    { field: 'commonName', label: 'Name' },
    { field: 'xrefAOPWikiKEID', label: 'AOPWiki KE ID' },
  ],
  Disease: [{ field: 'commonName', label: 'Name' }],
  Assay: [{ field: 'commonName', label: 'Name' }],
  ChemicalList: [{ field: 'commonName', label: 'Name' }],
};

const OPERATORS = [
  { value: 'eq', label: 'equals' },
  { value: 'contains', label: 'contains' },
  { value: 'startsWith', label: 'starts with' },
];

function emptyNode(nodeType) {
  return { kind: 'node', nodeType: nodeType || '', filters: [] };
}

function emptyRel() {
  return { kind: 'rel', relType: '', display: '' };
}

function NodeChip({ step, index, edgeSchema, onUpdate, onRemoveHop, isLast, totalNodes }) {
  const color = NODE_COLORS[step.nodeType] || '#e0e0e0';
  const fields = NODE_FIELDS[step.nodeType] || [];
  const hasFilters = step.filters.length > 0;

  const handleAddFilter = () => {
    const updated = {
      ...step,
      filters: [...step.filters, { field: fields[0]?.field || '', op: 'eq', value: '' }],
    };
    onUpdate(index, updated);
  };

  const handleRemoveFilter = (fi) => {
    const updated = {
      ...step,
      filters: step.filters.filter((_, i) => i !== fi),
    };
    onUpdate(index, updated);
  };

  const handleFilterChange = (fi, key, val) => {
    const newFilters = step.filters.map((f, i) =>
      i === fi ? { ...f, [key]: val } : f
    );
    onUpdate(index, { ...step, filters: newFilters });
  };

  const handleTypeChange = (e) => {
    onUpdate(index, { ...step, nodeType: e.target.value, filters: [] });
  };

  const availableTypes = useMemo(() => {
    if (!edgeSchema) return [];
    return edgeSchema.nodeTypes || [];
  }, [edgeSchema]);

  return (
    <Paper
      elevation={1}
      sx={{
        px: 1.5,
        py: 1,
        borderTop: `3px solid ${color}`,
        display: 'flex',
        flexDirection: 'column',
        gap: 0.75,
        position: 'relative',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
        <FormControl size="small" sx={{ minWidth: 110 }}>
          <Select
            value={step.nodeType}
            onChange={handleTypeChange}
            displayEmpty
            renderValue={(v) =>
              v ? (
                <Chip size="small" label={v} sx={{ backgroundColor: NODE_COLORS[v], fontWeight: 600, height: 22, fontSize: '0.75rem' }} />
              ) : (
                <Typography variant="caption" color="text.secondary">Node type</Typography>
              )
            }
            sx={{ '.MuiSelect-select': { py: 0.5 } }}
          >
            {availableTypes.map((t) => (
              <MenuItem key={t} value={t} dense>
                <Chip size="small" label={t} sx={{ backgroundColor: NODE_COLORS[t], fontWeight: 600, height: 20, fontSize: '0.7rem' }} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {step.nodeType && !hasFilters && (
          <Button size="small" onClick={handleAddFilter} sx={{ textTransform: 'none', fontSize: '0.7rem', minWidth: 0, px: 0.5, whiteSpace: 'nowrap' }}>
            + filter
          </Button>
        )}

        {totalNodes > 1 && isLast && (
          <IconButton size="small" onClick={onRemoveHop} sx={{ p: 0.25 }}>
            <CloseIcon sx={{ fontSize: 16 }} />
          </IconButton>
        )}
      </Box>

      {step.filters.map((f, fi) => (
        <Box key={fi} sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 80 }}>
            <Select
              value={f.field}
              onChange={(e) => handleFilterChange(fi, 'field', e.target.value)}
              displayEmpty
              sx={{ fontSize: '0.8rem', '.MuiSelect-select': { py: 0.4 } }}
            >
              {fields.map((fld) => (
                <MenuItem key={fld.field} value={fld.field} dense>{fld.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 64 }}>
            <Select
              value={f.op}
              onChange={(e) => handleFilterChange(fi, 'op', e.target.value)}
              sx={{ fontSize: '0.8rem', '.MuiSelect-select': { py: 0.4 } }}
            >
              {OPERATORS.map((op) => (
                <MenuItem key={op.value} value={op.value} dense>{op.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            size="small"
            placeholder="value"
            value={f.value}
            onChange={(e) => handleFilterChange(fi, 'value', e.target.value)}
            sx={{ width: 90, '& .MuiInputBase-input': { py: 0.5, fontSize: '0.8rem' } }}
          />
          <IconButton size="small" onClick={() => handleRemoveFilter(fi)} sx={{ p: 0.25 }}>
            <CloseIcon sx={{ fontSize: 14 }} />
          </IconButton>
        </Box>
      ))}

      {hasFilters && step.nodeType && (
        <Button size="small" onClick={handleAddFilter} sx={{ textTransform: 'none', fontSize: '0.7rem', minWidth: 0, px: 0.5, py: 0, alignSelf: 'flex-start' }}>
          + filter
        </Button>
      )}
    </Paper>
  );
}

function RelConnector({ step, index, sourceType, edgeSchema, onUpdate }) {
  const availableRels = useMemo(() => {
    if (!edgeSchema || !sourceType) return [];
    return edgeSchema.edges.filter((e) => e.source === sourceType);
  }, [edgeSchema, sourceType]);

  const handleChange = (e) => {
    const selected = availableRels.find((r) =>
      `${r.rel}::${r.target}` === e.target.value
    );
    if (selected) {
      onUpdate(index, {
        ...step,
        relType: selected.rel,
        display: selected.display,
        _targetType: selected.target,
      });
    }
  };

  const currentValue = step.relType && step._targetType
    ? `${step.relType}::${step._targetType}`
    : '';

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <ArrowForwardIcon sx={{ color: '#aaa', fontSize: 18 }} />
      <FormControl size="small" sx={{ minWidth: 130 }}>
        <Select
          value={currentValue}
          onChange={handleChange}
          displayEmpty
          renderValue={(v) => {
            if (!v) return <Typography variant="caption" color="text.secondary">relationship</Typography>;
            const match = availableRels.find((r) => `${r.rel}::${r.target}` === v);
            return <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>{match?.display || v}</Typography>;
          }}
          sx={{ fontSize: '0.8rem', '.MuiSelect-select': { py: 0.4 } }}
        >
          {availableRels.map((r) => (
            <MenuItem key={`${r.rel}::${r.target}`} value={`${r.rel}::${r.target}`} dense>
              {r.display}
              <Typography variant="caption" sx={{ ml: 0.5, color: 'text.secondary' }}>
                → {r.target}
              </Typography>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <ArrowForwardIcon sx={{ color: '#aaa', fontSize: 18 }} />
    </Box>
  );
}

function NodeDetail({ node, config }) {
  const identifiers = node.identifiers || [];
  const features = node.nodeFeatures || [];

  return (
    <Box sx={{ py: 1 }}>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        <Chip size="small" label={node.nodeType} sx={{ backgroundColor: NODE_COLORS[node.nodeType], fontWeight: 600, height: 20, fontSize: '0.7rem', mr: 0.5 }} />
        {node.commonName || 'Unnamed'}
      </Typography>
      <Grid container spacing={2}>
        {identifiers.length > 0 && (
          <Grid item xs={6}>
            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Identifiers</Typography>
            <Table size="small" sx={{ '& td, & th': { py: 0.25, px: 0.5, fontSize: '0.75rem' } }}>
              <TableBody>
                {identifiers.map((id) => (
                  <TableRow key={id.idType}>
                    <TableCell sx={{ color: 'text.secondary' }}>{config?.nodeConfig?.translateIdType?.[id.idType] || id.idType}</TableCell>
                    <TableCell>{id.idValue}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Grid>
        )}
        {features.length > 0 && (
          <Grid item xs={identifiers.length > 0 ? 6 : 12}>
            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Properties</Typography>
            <Table size="small" sx={{ '& td, & th': { py: 0.25, px: 0.5, fontSize: '0.75rem' } }}>
              <TableBody>
                {features.map((f) => (
                  <TableRow key={f.featType}>
                    <TableCell sx={{ color: 'text.secondary' }}>{f.featType}</TableCell>
                    <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.featValue}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Grid>
        )}
      </Grid>
      {node.ontologyIRI && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
          IRI: {node.ontologyIRI}
        </Typography>
      )}
    </Box>
  );
}

function ResultRow({ row, relLabels, relTypes, config, onQueryFromNode }) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState('details');

  const seedEdges = useMemo(() => {
    if (row.length < 2) return [];
    return (relTypes || []).map((rt, i) => ({
      source: row[i].nodeId,
      target: row[i + 1].nodeId,
      relType: rt,
    }));
  }, [row, relTypes]);

  return (
    <>
      <TableRow hover onClick={() => setOpen(!open)} sx={{ cursor: 'pointer', '& > td': { borderBottom: open ? 'none' : undefined } }}>
        <TableCell sx={{ width: 30, p: 0.5 }}>
          <IconButton size="small" sx={{ p: 0.25 }}>
            {open ? <KeyboardArrowUpIcon fontSize="small" /> : <KeyboardArrowDownIcon fontSize="small" />}
          </IconButton>
        </TableCell>
        <TableCell colSpan={row.length + relLabels.length} sx={{ p: 0.75 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0.5 }}>
            {row.map((node, ci) => (
              <React.Fragment key={ci}>
                {ci > 0 && relLabels[ci - 1] && (
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic', mx: 0.25 }}>
                    —{relLabels[ci - 1]}→
                  </Typography>
                )}
                <Chip
                  size="small"
                  label={node.nodeType}
                  sx={{ backgroundColor: NODE_COLORS[node.nodeType], fontWeight: 600, fontSize: '0.65rem', height: 18 }}
                />
                <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                  {node.commonName || node.nodeFeatures?.[0]?.featValue || `ID: ${node.nodeId}`}
                </Typography>
              </React.Fragment>
            ))}
          </Box>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell sx={{ p: 0 }} />
        <TableCell colSpan={row.length + relLabels.length} sx={{ p: 0 }}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ backgroundColor: '#fafafa', borderBottom: '1px solid #eee' }}>
              <Box sx={{ display: 'flex', gap: 0.5, px: 1, pt: 0.5 }}>
                <Button
                  size="small"
                  variant={view === 'details' ? 'contained' : 'text'}
                  onClick={(e) => { e.stopPropagation(); setView('details'); }}
                  sx={{ textTransform: 'none', fontSize: '0.75rem', minWidth: 0, px: 1, py: 0.25 }}
                >
                  Details
                </Button>
                <Button
                  size="small"
                  variant={view === 'explore' ? 'contained' : 'text'}
                  onClick={(e) => { e.stopPropagation(); setView('explore'); }}
                  sx={{ textTransform: 'none', fontSize: '0.75rem', minWidth: 0, px: 1, py: 0.25 }}
                >
                  Explore
                </Button>
              </Box>

              {view === 'details' && (
                <Box sx={{ px: 1, py: 0.5 }}>
                  {row.map((node, ci) => (
                    <React.Fragment key={ci}>
                      {ci > 0 && (
                        <Box sx={{ display: 'flex', alignItems: 'center', py: 0.5, pl: 2 }}>
                          <ArrowForwardIcon sx={{ fontSize: 14, color: '#aaa', mr: 0.5 }} />
                          <Typography variant="caption" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                            {relLabels[ci - 1] || 'related to'}
                          </Typography>
                        </Box>
                      )}
                      <NodeDetail node={node} config={config} />
                    </React.Fragment>
                  ))}
                </Box>
              )}

              {view === 'explore' && (
                <Box sx={{ px: 1, py: 0.5 }}>
                  <GraphExplorer
                    seedNodes={row}
                    seedEdges={seedEdges}
                    onQueryFromNode={onQueryFromNode}
                  />
                </Box>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

function ResultsTable({ results, relLabels, relTypes, config, onQueryFromNode }) {
  if (!results || results.length === 0) return null;

  return (
    <Box sx={{ mt: 1.5 }}>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        {results.length} result{results.length !== 1 ? 's' : ''} found
      </Typography>
      <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
        <Table size="small">
          <TableBody>
            {results.map((row, ri) => (
              <ResultRow key={ri} row={row} relLabels={relLabels} relTypes={relTypes || []} config={config} onQueryFromNode={onQueryFromNode} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function ContinuationRow({ children }) {
  return (
    <Box sx={{ display: 'flex', ml: 2, mt: -0.5 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', width: 20, mr: 1, flexShrink: 0 }}>
        <Box sx={{ borderLeft: '2px solid #ccc', flex: 1, minHeight: 8 }} />
        <Box sx={{ borderLeft: '2px solid #ccc', borderBottom: '2px solid #ccc', borderBottomLeftRadius: 8, height: '50%', minHeight: 12 }} />
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.75 }}>
        {children}
      </Box>
    </Box>
  );
}

const EXAMPLE_PATTERN = [
  { kind: 'node', nodeType: 'Chemical', filters: [] },
  { kind: 'rel', relType: 'chemicalIncreasesExpression', display: 'increases expression of', _targetType: 'Gene' },
  { kind: 'node', nodeType: 'Gene', filters: [{ field: 'geneSymbol', op: 'eq', value: 'CYP2E1' }] },
  { kind: 'rel', relType: 'geneInPathway', display: 'participates in', _targetType: 'Pathway' },
  { kind: 'node', nodeType: 'Pathway', filters: [] },
];

const QueryBuilder = ({ config }) => {
  const { data: edgeSchema, isLoading: schemaLoading } = useFetchEdgeSchemaQuery();
  const [executePattern, { isLoading: queryLoading }] = useExecutePatternMutation();

  const [steps, setSteps] = useState([emptyNode('Chemical')]);
  const [results, setResults] = useState(null);
  const [resultRelLabels, setResultRelLabels] = useState([]);
  const [resultRelTypes, setResultRelTypes] = useState([]);
  const [error, setError] = useState(null);

  const updateStep = useCallback((index, newStep) => {
    setSteps((prev) => {
      const next = [...prev];
      next[index] = newStep;

      if (newStep.kind === 'rel' && newStep._targetType) {
        const nextNodeIndex = index + 1;
        if (next[nextNodeIndex]) {
          next[nextNodeIndex] = { ...next[nextNodeIndex], nodeType: newStep._targetType };
        }
      }

      return next;
    });
  }, []);

  const addHop = useCallback(() => {
    setSteps((prev) => [...prev, emptyRel(), emptyNode('')]);
  }, []);

  const removeLastHop = useCallback(() => {
    setSteps((prev) => {
      if (prev.length <= 1) return prev;
      return prev.slice(0, -2);
    });
  }, []);

  const handleSearch = useCallback(async () => {
    setError(null);
    setResults(null);
    setResultRelLabels([]);

    const nodeSteps = steps.filter((s) => s.kind === 'node');
    const relSteps = steps.filter((s) => s.kind === 'rel');

    for (const ns of nodeSteps) {
      if (!ns.nodeType) {
        setError('All node slots must have a type selected.');
        return;
      }
    }

    for (const rs of relSteps) {
      if (!rs.relType) {
        setError('All relationship slots must be filled.');
        return;
      }
    }

    if (nodeSteps.length === 1 && nodeSteps[0].filters.every((f) => !f.value.trim())) {
      setError('Add at least one filter when searching for a single node type.');
      return;
    }

    const pattern = steps.map((s) =>
      s.kind === 'node'
        ? { nodeType: s.nodeType, filters: s.filters.filter((f) => f.value.trim() !== '') }
        : { relType: s.relType }
    );

    try {
      const res = await executePattern(pattern).unwrap();
      setResults(res.results);
      setResultRelLabels(relSteps.map((r) => r.display || r.relType));
      setResultRelTypes(relSteps.map((r) => r.relType));
    } catch (err) {
      setError(err.data?.message || 'Query failed. Check your pattern and try again.');
    }
  }, [steps, executePattern]);

  const loadExample = useCallback(() => {
    setSteps(EXAMPLE_PATTERN);
    setResults(null);
    setResultRelLabels([]);
    setResultRelTypes([]);
    setError(null);
  }, []);

  const handleClear = useCallback(() => {
    setSteps([emptyNode('Chemical')]);
    setResults(null);
    setResultRelLabels([]);
    setResultRelTypes([]);
    setError(null);
  }, []);

  const handleQueryFromNode = useCallback((node) => {
    const nodeType = node.nodeType || '';
    const nameField = nodeType === 'Gene' ? 'geneSymbol'
      : nodeType === 'KeyEvent' ? 'keyEventName'
      : 'commonName';
    const nameValue = nodeType === 'Gene'
      ? (node.nodeFeatures?.find((f) => f.featType === 'geneSymbol')?.featValue || node.commonName || '')
      : (node.commonName || '');

    setSteps([{
      kind: 'node',
      nodeType,
      filters: nameValue ? [{ field: nameField, op: 'eq', value: nameValue }] : [],
    }]);
    setResults(null);
    setResultRelLabels([]);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  if (schemaLoading) {
    return (
      <div className="subject-container">
        <h2>Query Builder</h2>
        <CircularProgress size={24} />
      </div>
    );
  }

  const nodeSteps = steps.filter((s) => s.kind === 'node');
  const totalNodes = nodeSteps.length;
  const lastNodeType = nodeSteps[nodeSteps.length - 1]?.nodeType;
  const canAddHop = lastNodeType && edgeSchema?.edges.some((e) => e.source === lastNodeType);

  return (
    <div className="subject-container">
      <h2>Query Builder</h2>
      <Typography variant="body2" sx={{ mb: 1, fontStyle: 'italic' }}>
        Build a multi-hop graph pattern to search the knowledge graph.
        Select node types, choose how they are connected, and add optional
        filters on node properties.
      </Typography>

      <Box
        sx={{
          px: 2,
          py: 1.5,
          border: '1px solid #ddd',
          borderRadius: 1,
          backgroundColor: '#fafafa',
          mb: 1.5,
        }}
      >
        {(() => {
          const nodeStepsList = steps.filter((s) => s.kind === 'node');
          const relStepsList = steps.filter((s) => s.kind === 'rel');
          const rows = [];

          if (nodeStepsList.length === 1 && relStepsList.length === 0) {
            rows.push(
              <Box key="row-0" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <NodeChip step={steps[0]} index={0} edgeSchema={edgeSchema} onUpdate={updateStep} onRemoveHop={removeLastHop} isLast totalNodes={totalNodes} />
                {canAddHop && (
                  <Tooltip title="Add a relationship hop">
                    <IconButton onClick={addHop} color="primary" size="small">
                      <AddCircleOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            );
          } else {
            rows.push(
              <Box key="row-0" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <NodeChip step={steps[0]} index={0} edgeSchema={edgeSchema} onUpdate={updateStep} onRemoveHop={removeLastHop} isLast={false} totalNodes={totalNodes} />
                <RelConnector step={steps[1]} index={1} sourceType={steps[0].nodeType} edgeSchema={edgeSchema} onUpdate={updateStep} />
                <NodeChip step={steps[2]} index={2} edgeSchema={edgeSchema} onUpdate={updateStep} onRemoveHop={removeLastHop} isLast={relStepsList.length === 1} totalNodes={totalNodes} />
                {relStepsList.length === 1 && canAddHop && (
                  <Tooltip title="Add a relationship hop">
                    <IconButton onClick={addHop} color="primary" size="small">
                      <AddCircleOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            );

            for (let hop = 1; hop < relStepsList.length; hop++) {
              const relIdx = hop * 2 + 1;
              const nodeIdx = hop * 2 + 2;
              const isLastHop = hop === relStepsList.length - 1;
              const prevNodeType = steps[relIdx - 1]?.nodeType;

              rows.push(
                <ContinuationRow key={`hop-${hop}`}>
                  <RelConnector step={steps[relIdx]} index={relIdx} sourceType={prevNodeType} edgeSchema={edgeSchema} onUpdate={updateStep} />
                  <NodeChip step={steps[nodeIdx]} index={nodeIdx} edgeSchema={edgeSchema} onUpdate={updateStep} onRemoveHop={removeLastHop} isLast={isLastHop} totalNodes={totalNodes} />
                  {isLastHop && canAddHop && (
                    <Tooltip title="Add a relationship hop">
                      <IconButton onClick={addHop} color="primary" size="small">
                        <AddCircleOutlineIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </ContinuationRow>
              );
            }
          }

          return rows;
        })()}
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={queryLoading ? <CircularProgress size={18} color="inherit" /> : <SearchIcon />}
          onClick={handleSearch}
          disabled={queryLoading}
        >
          Search
        </Button>
        <Button variant="outlined" onClick={loadExample}>
          Load example
        </Button>
        <Button variant="outlined" onClick={handleClear}>
          Clear
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {results && <ResultsTable results={results} relLabels={resultRelLabels} relTypes={resultRelTypes} config={config} onQueryFromNode={handleQueryFromNode} />}
    </div>
  );
};

export default QueryBuilder;
