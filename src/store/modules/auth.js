const state = {
  accessToken: localStorage.getItem('accessToken') || null,
};

const getters = {
  isAuthenticated: state => !!state.accessToken,
  getAccessToken: state => state.accessToken
};

const actions = {
  login({ commit }, token) {
    commit('setAccessToken', token);
  },
};

const mutations = {
  setAccessToken(state, accessToken) {
    state.accessToken = accessToken;
    localStorage.setItem('accessToken', accessToken);
  },
};

export default {
  state,
  getters,
  actions,
  mutations
};
