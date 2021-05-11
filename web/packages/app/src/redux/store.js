import { configureStore } from '@reduxjs/toolkit';

import nodeSearchReducer from '../components/nodeSearch/nodeSearchSlice';

export const store = configureStore({
  reducer: {
    nodeSearch: nodeSearchReducer,
    //relSearch: relSearchReducer,
    //pathSearch: pathSearchReducer,
    //bulkData: bulkDataReducer,
  },
});
