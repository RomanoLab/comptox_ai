/**
 * This slice handles state related to both individual nodes and sets of nodes
 * retrieved through searches on the Web API.
 */

import { createSlice } from '@reduxjs/toolkit';

export const nodeSlice = createSlice({
  name: 'node',
  initialState: {
    selectedNode: null,
    searchResults: [],
    searchParams: {
      searchType: null,
      params: {}
    }
  },
  reducers: {
    selectNode: (state, action) => {
      state.selectedNode = action.payload;
    },
    readSearchResults: (state, action) => {
      state.searchResults = action.payload;
    },
    setSearchStatus: (state, action) => {
      state.searchStatus = action.payload;
    },
    setSearch: (state, action) => {
      state.searchParams = action.payload;
    }
  }
});

export const { selectNode, readSearchResults, setSearchStatus, setSearch } = nodeSlice.actions;

export default nodeSlice.reducer;
