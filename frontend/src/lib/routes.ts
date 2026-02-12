export const routes = {
  home: "/",
  login: "/login",
  register: "/register",
  verify: "/verify",
  profile: "/profile",
  admin: {
    dashboard: "/admin/dashboard",
    cities: "/admin/cities",
  },
} as const;
