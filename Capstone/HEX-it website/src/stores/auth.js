// stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: false,
        user: null,
        token: null
    }),
    actions: {
        login(userData, token) {
            this.isAuthenticated = true;
            this.user = userData;
            this.token = token;
            localStorage.setItem('authToken', token);
            if (userData) {
                localStorage.setItem('user_data', JSON.stringify(userData));
            }
        },
        logout() {
            this.isAuthenticated = false;
            this.user = null;
            this.token = null;
            localStorage.removeItem('authToken');
            localStorage.removeItem('user_data');
        },
        checkAuth() {
            const token = localStorage.getItem('auth_token');
            
            if (token) {
                this.isAuthenticated = true;
                this.token = token;
                
                // Try to get user data
                const userData = localStorage.getItem('user_data');
                if (userData) {
                    try {
                        this.user = JSON.parse(userData);
                    } catch (e) {
                        console.error('Failed to parse user data from localStorage:', e);
                        // Create a minimal user object if parsing fails
                        if (!this.user) this.user = { id: this.extractUserIdFromToken(token) };
                    }
                } else {
                    // If no user data but we have a token, create a minimal user object
                    if (!this.user) this.user = { id: this.extractUserIdFromToken(token) };
                }
                
                return true; // We have a token, so we're authenticated
            }
            
            this.isAuthenticated = false;
            return false;
        },
        
        // Extract user ID from JWT token
        extractUserIdFromToken(token) {
            try {
                // JWT tokens are in the format: header.payload.signature
                const parts = token.split('.');
                if (parts.length !== 3) return null;
                
                // Decode the payload (middle part)
                const payload = JSON.parse(atob(parts[1]));
                
                // JWT might store user ID as 'sub', 'id', or 'userId'
                return payload.sub || payload.id || payload.userId || null;
            } catch (e) {
                console.error('Failed to extract user ID from token:', e);
                return null;
            }
        },
        
        // Method to manually set user data
        setUserData(userData) {
            this.user = userData;
            if (userData) {
                localStorage.setItem('user_data', JSON.stringify(userData));
            }
        },
        
        // Method to decode and get payload from JWT token
        getTokenPayload() {
            if (!this.token) return null;
            
            try {
                const parts = this.token.split('.');
                if (parts.length !== 3) return null;
                
                return JSON.parse(atob(parts[1]));
            } catch (e) {
                console.error('Failed to decode token payload:', e);
                return null;
            }
        }
    }
})