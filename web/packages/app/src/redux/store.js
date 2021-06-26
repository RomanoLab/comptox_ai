import { configureStore } from '@reduxjs/toolkit';

import nodeSlice from '../features/nodes/nodeSlice';
import { comptoxApiSlice } from '../features/comptoxApi/comptoxApiSlice';

export const store = configureStore({
  reducer: {
    node: nodeSlice,
    [comptoxApiSlice.reducerPath]: comptoxApiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware().concat(comptoxApiSlice.middleware);
  }
});
