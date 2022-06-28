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
  },
  reducers: {
    selectNode: (state, action) => {
      state.selectedNode = action.payload
    },
    readSearchResults: (state, action) => {
      state.searchResults = action.payload
    }
  },
})

export const { selectNode, readSearchResults } = nodeSlice.actions

export default nodeSlice.reducer
