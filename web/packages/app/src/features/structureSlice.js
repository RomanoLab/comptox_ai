import { createSlice } from '@reduxjs/toolkit';

export const structureSlice = createSlice({
    name: 'structure',
    initialState: {
        currentMolData: "",
        retrievedStructures: [],
        selectedStructure: null
    },
    reducers: {
        setCurrentMolData: (state, action) => {
            state.currentMolData = action.payload
        },
        selectStructure: (state, action) => {
            state.selectedStructure = action.payload
        },
        readStructureSearchResults: (state, action) => {
            state.retrievedStructures = action.payload
        }
    }
});

export const { setCurrentMolData, selectStructure, readStructureSearchResults } = structureSlice.actions;

export default structureSlice.reducer;
