import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { combineSlices, configureStore } from "@reduxjs/toolkit";
import authReducer from "./features/auth/authSlice";
import { authApi } from "./features/auth/authApi";
import { studentsApi } from "./features/users/students/studentsApi";
import { teachersApi } from "./features/users/teachers/teachersApi";
import { registrationApi } from "./features/registration/registrationApi";

const rootReducer = combineSlices(authApi, studentsApi, teachersApi, registrationApi, {
  auth: authReducer,
});

export type RootState = ReturnType<typeof rootReducer>;

export const makeStore = () => {
  return configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(
        authApi.middleware,
        studentsApi.middleware,
        teachersApi.middleware,
        registrationApi.middleware,
      ),
  });
};

export type AppStore = ReturnType<typeof makeStore>;
export type AppDispatch = AppStore["dispatch"];
export type AppThunk<ThunkReturnType = void> = ThunkAction<
  ThunkReturnType,
  RootState,
  unknown,
  Action
>;
