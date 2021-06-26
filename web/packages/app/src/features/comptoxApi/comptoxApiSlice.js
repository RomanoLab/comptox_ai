import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const comptoxApiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://comptox.ai/api' }),
  endpoints: (builder) => ({
    fetchConfig: builder.query({
      query: () => `/config`,
    }),
    searchNodes: builder.query({
      query: (label, field, value) => `/nodes/${label}/search?field=${field}&value=${value}`,
    }),
  })
});

export const { useFetchConfigQuery, useSearchNodesQuery } = comptoxApiSlice;
