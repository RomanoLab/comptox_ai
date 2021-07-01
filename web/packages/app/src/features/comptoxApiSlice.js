import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const comptoxApiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:3000' }),
  endpoints: (builder) => ({
    fetchConfig: builder.query({
      query: () => `/config`,
    }),
    searchNodes: builder.query({
      query: (label) => `/nodes/${label[0]}/search?field=${label[1]}&value=${label[2]}`
    }),
    searchNodesContains: builder.query({
      query: (label, contains) => {
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
  })
});

export const {
  useFetchConfigQuery,
  useSearchNodesQuery,
  useSearchNodesContainsQuery,
  useFetchRelationshipsByNodeIdQuery,
  useFindPathByNodeIdsQuery
} = comptoxApiSlice;
