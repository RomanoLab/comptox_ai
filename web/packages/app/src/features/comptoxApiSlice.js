import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const HOST = (process.env.NODE_ENV === 'production') ? 'https://comptox.ai/api' : 'http://localhost:3000';

export const comptoxApiSlice = createApi({
  reducerPath: 'api',
  // baseQuery: fetchBaseQuery({ baseUrl: 'https://comptox.ai/api' }),
  baseQuery: fetchBaseQuery({ baseUrl: HOST }),
  endpoints: (builder) => ({
    fetchConfig: builder.query({
      query: () => `/config`,
    }),
    searchNodes: builder.query({
      query: (label) => `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
    }),
    searchNodesContains: builder.query({
      query: (label) => {
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
    runStructureSearch: builder.query({
      query: (searchData) => ({
        url: '/chemicals/structureSearch',
        method: 'POST',
        body: searchData
      })
    })
  })
});

export const {
  endpoints,
  useFetchConfigQuery,
  useSearchNodesQuery,
  useSearchNodesContainsQuery,
  useFetchRelationshipsByNodeIdQuery,
  useFindPathByNodeIdsQuery,
  useMakeQsarDatasetQuery,
  useRunStructureSearchQuery
} = comptoxApiSlice;
