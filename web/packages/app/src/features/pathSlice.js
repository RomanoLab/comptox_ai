import { createSlice } from '@reduxjs/toolkit';

export const pathSlice = createSlice({
  name: 'path',
  initialState: {
    pathStartNodeId: null,
    pathEndNodeId: null,
  },
  reducers: {
    setPathStartNodeId: (state, action) => {
      state.pathStartNodeId = action.payload
    },
    setPathEndNodeId: (state, action) => {
      state.pathEndNodeId = action.payload
    }
  }
})

export const { setPathStartNodeId, setPathEndNodeId } = pathSlice.actions;

export default pathSlice.reducer;