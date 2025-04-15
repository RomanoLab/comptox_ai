import { configureStore } from '@reduxjs/toolkit';

import { comptoxApiSlice } from '../features/comptoxApiSlice';
import modulesSlice from '../features/modulesSlice';
import nodeSlice from '../features/nodeSlice';
import pathSlice from '../features/pathSlice';
import relationshipSlice from '../features/relationshipSlice';
import structureSlice from '../features/structureSlice';


export const store = configureStore({
  reducer: {
    node: nodeSlice,
    relationship: relationshipSlice,
    path: pathSlice,
    modules: modulesSlice,
    structures: structureSlice,
    [comptoxApiSlice.reducerPath]: comptoxApiSlice.reducer
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware().concat(comptoxApiSlice.middleware);
  }
});
