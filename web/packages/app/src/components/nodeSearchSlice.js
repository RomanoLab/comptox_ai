import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
//import { comptoxAPI } from '../../API'  <- This file doesn't exist yet

// NOTE: This is just for testing purposes!
class comptoxAPI {
  fetchNodesBySearchQuery() {
    return ({'hello': 'there'});
  }
}

const fetchNodesBySearchQuery = createAsyncThunk(
  'nodes/fetchBySearchQuery',
  async (searchParams, thunkAPI) => {
    const response = await comptoxAPI.fetchNodesBySearchQuery(
      searchParams.nodeLabels,
      searchParams.searchField,
      searchParams.searchFieldValue
    );
    return response.data
  }
)

const nodeSearchSlice = createSlice({
  name: 'nodeSearch',
  initialState: {
    returnedNodes: [],
    loading: 'idle'
  },
  reducers: {
  },
  extraReducers: {
    [fetchNodesBySearchQuery.fulfilled]: (state, action) => {
      state.returnedNodes.push(action.payload);
    }
  }
});

export default nodeSearchSlice;
