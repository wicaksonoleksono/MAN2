import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { combineSlices, configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/auth";
import { authApi } from "@/api/auth";
import { studentsApi } from "@/api/students";
import { teachersApi } from "@/api/teachers";
import { registrationApi } from "@/api/registration";

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
