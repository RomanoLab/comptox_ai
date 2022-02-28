import { createSlice } from '@reduxjs/toolkit';

export const modulesSlice = createSlice({
    name: 'modules',
    initialState: {
        shortestPathStart: null,
        shortestPathEnd: null,
        expandNetworkNode: null,
    },
    reducers: {
        setShortestPathStartNode: (state, action) => {
            state.shortestPathStart = action.payload
        },
        setShortestPathEndNode: (state, action) => {
            state.shortestPathEnd = action.payload
        },
        setExpandNetworkNode: (state, action) => {
            state.expandNetworkNode = action.payload
        }
    },
})

export const { 
    setShortestPathStartNode,
    setShortestPathEndNode,
    setExpandNetworkNode
} = modulesSlice.actions

export default modulesSlice.reducer
