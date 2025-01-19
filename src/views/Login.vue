<template>
  <div class="login-page">
    <div class="login-container">
      <div
        v-if="error"
        class="error-message"
      >
        {{ error }}
      </div>
      <form @submit.prevent="handleSubmit">
        <input
          v-model="username"
          type="text"
          placeholder="Username"
        >
        <input
          v-model="password"
          type="password"
          placeholder="Password"
        >
        <input
          type="submit"
          value="Login"
        >
      </form>
    </div>
  </div>
</template>

<script>
import {mapActions} from "vuex";
import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: null,
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleSubmit() {
      try {
        const response = await axios.post('/api/token', new URLSearchParams({
          username: this.username,
          password: this.password
        }).toString(), {
          headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        });
        this.login(response.data.access_token);
        this.$router.push('/'); // redirect to home page
      } catch (error) {
        // Handle error
        this.error = error.response.data.detail;
      }
    }
  }
}
</script>
<style>

.login-container {
    max-width: 300px;
    padding: 20px;
    background-color: #ffffff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

.error-message {
    color: #dc3545;
    margin-bottom: 20px;
}

.login-page {
    font-family: Arial, sans-serif;
    background-color: #f8f9fa;
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.login-container form {
    margin-top: 20px;
}

.login-container input {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    box-sizing: border-box;
    border: 1px solid #ced4da;
    border-radius: 4px;
}

.login-container input[type="submit"] {
    background-color: #007bff;
    color: #fff;
    cursor: pointer;
}

.login-container input[type="submit"]:hover {
    background-color: #0056b3;
}

</style>
