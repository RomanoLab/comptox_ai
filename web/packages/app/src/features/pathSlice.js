import { createSlice } from '@reduxjs/toolkit';

export const pathSlice = createSlice({
  name: 'path',
  initialState: {
    pathStartNodeId: null,
    pathEndNodeId: null
  },
  reducers: {
    setPathStartNodeId: (state, action) => {
      state.pathStartNodeId = action.payload;
    },
    setPathStartNodeName: (state, action) => {
      state.pathStartNodeName = action.payload;
    },
    setPathEndNodeId: (state, action) => {
      state.pathEndNodeId = action.payload;
    },
    setPathEndNodeName: (state, action) => {
      state.pathEndNodeName = action.payload;
    }
  }
});

export const { setPathStartNodeId, setPathStartNodeName, setPathEndNodeId, setPathEndNodeName } = pathSlice.actions;

export default pathSlice.reducer;