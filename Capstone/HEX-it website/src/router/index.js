import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UserHomeView from '../views/UserHomeView.vue'
import MyProfileView from '../views/MyProfileView.vue'
import CreateProfileView from '../views/CreateProfileView.vue'
import LoginForm from '../components/LoginForm.vue'
import SignUpForm from '../components/SignUpForm.vue'
import MatchProfilesView from '../views/MatchProfilesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/home',
      name: 'userHome',
      component: UserHomeView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
    },
    {
      path: '/register',
      name: 'register',
      component: SignUpForm
    },
    {
      path: '/profile',
      name: 'profile',
      component: MyProfileView
    },
    {
      path: '/create',
      name: 'create',
      component: CreateProfileView,
    },
    {
      path: '/profiles/:id',
      name: 'profileDetail',
      component: () => import('../views/ProfileDetailView.vue'),
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/edit-profile/:id',
      name: 'editProfile',
      component: () => import('../views/EditProfileView.vue'),
      meta: { requiresAuth: true }
    },
    // {
    //   path: '/edit-user-profile/:id',
    //   name: 'editUserProfile',
    //   component: () => import('../views/EditUserProfileView.vue'),
    //   meta: { requiresAuth: true }
    // },
    {
      path: '/profiles/matches/:id',
      name: 'matchReport',
      component: () => import('../views/MatchProfilesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profiles/:id/matches',
      name: 'matchReport',
      component: MatchProfilesView
    }
  ]
})

export default router
