import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const comptoxApiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://comptox.ai/api' }),
  endpoints: (builder) => ({
    fetchConfig: builder.query({
      query: () => `/config`,
    }),
    searchNodes: builder.query({
      query: (label) => `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
    }),
    searchNodesContains: builder.query({
      query: (label) => {
        // if (contains) {
        //   return `/nodes/${label[0]}/searchFuzzy?field=${label[1]}&value=${label[2]}`
        // } else {
        //   return `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
        // }
        return `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
      }
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
  })
});

export const {
  useFetchConfigQuery,
  useSearchNodesQuery,
  useSearchNodesContainsQuery,
  useFetchRelationshipsByNodeIdQuery,
  useFindPathByNodeIdsQuery,
  useMakeQsarDatasetQuery
} = comptoxApiSlice;
