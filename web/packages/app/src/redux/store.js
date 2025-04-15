import { configureStore } from '@reduxjs/toolkit';

import nodeSlice from '../features/nodeSlice';
import relationshipSlice from '../features/relationshipSlice';
import pathSlice from '../features/pathSlice';
import modulesSlice from '../features/modulesSlice';
import structureSlice from '../features/structureSlice';
import { comptoxApiSlice } from '../features/comptoxApiSlice';


export const store = configureStore({
  reducer: {
    node: nodeSlice,
    relationship: relationshipSlice,
    path: pathSlice,
    modules: modulesSlice,
    structures: structureSlice,
    [comptoxApiSlice.reducerPath]: comptoxApiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware().concat(comptoxApiSlice.middleware);
  }
});
