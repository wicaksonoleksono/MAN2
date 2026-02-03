import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface User {
  user_id: string;
  username: string;
  created_at: string;
  last_login: string | null;
  is_active: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

// Load initial state from localStorage (if available)
const loadAuthFromStorage = (): AuthState => {
  if (typeof window === 'undefined') {
    return {
      token: null,
      user: null,
      isAuthenticated: false,
    };
  }

  try {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    return {
      token,
      user,
      isAuthenticated: !!token && !!user,
    };
  } catch (error) {
    console.error('Error loading auth from storage:', error);
    return {
      token: null,
      user: null,
      isAuthenticated: false,
    };
  }
};

const initialState: AuthState = loadAuthFromStorage();

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ token: string; user: User }>
    ) => {
      state.token = action.payload.token;
      state.user = action.payload.user;
      state.isAuthenticated = true;

      // Persist to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', action.payload.token);
        localStorage.setItem('user', JSON.stringify(action.payload.user));
      }
    },
    logout: (state) => {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;

      // Clear from localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
