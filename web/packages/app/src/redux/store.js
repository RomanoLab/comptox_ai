import { configureStore } from '@reduxjs/toolkit';

import nodeSlice from '../features/nodeSlice';
import relationshipSlice from '../features/relationshipSlice';
import { comptoxApiSlice } from '../features/comptoxApiSlice';

export const store = configureStore({
  reducer: {
    node: nodeSlice,
    relationship: relationshipSlice,
    [comptoxApiSlice.reducerPath]: comptoxApiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware().concat(comptoxApiSlice.middleware);
  }
});
