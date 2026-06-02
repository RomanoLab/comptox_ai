import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const HOST = import.meta.env.PROD ? 'https://api.comptox.ai' : 'http://localhost:3001';

export const comptoxApiSlice = createApi({
  reducerPath: 'api',
  // baseQuery: fetchBaseQuery({ baseUrl: 'https://comptox.ai/api' }),
  baseQuery: fetchBaseQuery({ baseUrl: HOST }),
  endpoints: (builder) => ({
    fetchConfig: builder.query({
      query: () => '/config'
    }),
    searchNodes: builder.query({
      query: (label) => `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
    }),
    searchNodesContains: builder.query({
      query: (label) => {
        return `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`;
      }
    }),
    fetchChemicalByDtsxid: builder.query({
      query: (dtsxid) => `/nodes/fetchChemicalByDtsxid/${dtsxid}`
    }),
    fetchRelationshipsByNodeId: builder.query({
      query: (nodeId) => `/relationships/fromStartNodeId/${nodeId}`
    }),
    findPathByNodeIds: builder.query({
      query: (nodeIds) => `/paths/findByIds?fromId=${nodeIds[0]}&toId=${nodeIds[1]}`
    }),
    makeQsarDataset: builder.query({
      query: (qsarParams) => `/datasets/makeQsarDataset?assay=${qsarParams[0]}&chemList=${qsarParams[1]}`
    }),
    runStructureSearch: builder.query({
      query: (searchData) => ({
        url: '/chemicals/structureSearch',
        method: 'POST',
        body: searchData
      })
    }),
    fetchEdgeSchema: builder.query({
      query: () => '/schema/edges'
    }),
    executePattern: builder.mutation({
      query: (pattern) => ({
        url: '/query/pattern',
        method: 'POST',
        body: { pattern }
      })
    }),
    fetchNeighborCounts: builder.query({
      query: (nodeId) => `/nodes/${nodeId}/neighborCounts`
    }),
    fetchNeighbors: builder.query({
      query: ({ nodeId, relType, limit }) => {
        let url = `/nodes/${nodeId}/neighbors`;
        const params = [];
        if (relType) params.push(`relType=${relType}`);
        if (limit) params.push(`limit=${limit}`);
        if (params.length) url += `?${params.join('&')}`;
        return url;
      }
    })
  })
});

export const {
  endpoints,
  useFetchConfigQuery,
  useSearchNodesQuery,
  useSearchNodesContainsQuery,
  useFetchChemicalByDtsxidQuery,
  useFetchRelationshipsByNodeIdQuery,
  useFindPathByNodeIdsQuery,
  useMakeQsarDatasetQuery,
  useRunStructureSearchQuery,
  useFetchEdgeSchemaQuery,
  useExecutePatternMutation,
  useLazyFetchNeighborCountsQuery,
  useLazyFetchNeighborsQuery
} = comptoxApiSlice;
