import { configureStore } from '@reduxjs/toolkit';

import nodeSlice from '../features/nodes/nodeSlice';

export const store = configureStore({
  reducer: {
    node: nodeSlice
    // relSearchResults: relSearchReducer,
    // pathSearchResults: pathSearchReducer,
    // bulkDataRequest: bulkDataReducer,
  },
});
