import { createSlice } from '@reduxjs/toolkit';

export const pathSlice = createSlice({
  name: 'path',
  initialState: {
    path: {},
  },
  reducers: {
    setPathData: (state, action) => {
      state.path = action.payload
    }
  }
})

export const { setPathData } = pathSlice.actions;

export default pathSlice.reducer;