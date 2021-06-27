import { createSlice } from '@reduxjs/toolkit';

export const relationshipSlice = createSlice({
  name: 'relationship',
  initialState: {
    relStartNode: {},
  },
  reducers: {
    setRelStartNode: (state, action) => {
      state.relStartNode = action.payload
    }
  },
})

export const { setRelStartNode } = relationshipSlice.actions

export default relationshipSlice.reducer
