import { createSlice } from '@reduxjs/toolkit';

export const nodeSlice = createSlice({
  name: 'nodes',
  initialState: {
    selectedNode: {
      "nodeId": 19,
      "nodeType": "Chemical",
      "commonName": "N-Ethyl-N-heptyl-4-hydroxy-4-{4-[(methanesulfonyl)amino]phenyl}butanamide",
      "identifiers": [
        {
          "idType": "xrefPubchemSID",
          "idValue": "316387445"
        },
        {
          "idType": "xrefDTXSID",
          "idValue": "DTXSID30857908"
        },
        {
          "idType": "xrefPubchemCID",
          "idValue": "71749683"
        },
        {
          "idType": "xrefCasRN",
          "idValue": "160087-98-9"
        }
      ],
      "ontologyIRI": "http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid30857908"
    },
    searchResults: [
      {
        "nodeId": 19,
        "nodeType": "Chemical",
        "commonName": "N-Ethyl-N-heptyl-4-hydroxy-4-{4-[(methanesulfonyl)amino]phenyl}butanamide",
        "identifiers": [
          {
            "idType": "xrefPubchemSID",
            "idValue": "316387445"
          },
          {
            "idType": "xrefDTXSID",
            "idValue": "DTXSID30857908"
          },
          {
            "idType": "xrefPubchemCID",
            "idValue": "71749683"
          },
          {
            "idType": "xrefCasRN",
            "idValue": "160087-98-9"
          }
        ],
        "ontologyIRI": "http://jdr.bio/ontologies/comptox.owl#chemical_dtxsid30857908"
      }
    ]
  },
  reducers: {
    selectNode: (state, action) => {
      state.selectedNode = action.payload
    },
  },
})

export const { selectNode } = nodeSlice.actions

export default nodeSlice.reducer
