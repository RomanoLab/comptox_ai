import { configureStore } from '@reduxjs/toolkit';

import nodeSearchSlice from '../components/nodeSearch/nodeSearchSlice';

export const store = configureStore({
  reducer: {
    nodeSearchResults: nodeSearchSlice,
    // relSearchResults: relSearchReducer,
    // pathSearchResults: pathSearchReducer,
    // bulkDataRequest: bulkDataReducer,
  },
});
