import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginForm from '../components/LoginForm.vue';
import AboutView from '../views/AboutView.vue';
import SignUpForm from '../components/SignUpForm.vue'; // Correctly import SignUpForm.vue

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginForm,
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView,
  },
  {
    path: '/register',
    name: 'Register',
    component: SignUpForm, // Use SignUpForm.vue for the /register route
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;