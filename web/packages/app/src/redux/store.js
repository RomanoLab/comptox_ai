import { configureStore } from '@reduxjs/toolkit';

import nodeSlice from '../features/nodes/nodeSlice';
import relationshipSlice from '../features/relationships/relationshipSlice';
import { comptoxApiSlice } from '../features/comptoxApi/comptoxApiSlice';

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
