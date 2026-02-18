export const routes = {
  home: "/",
  login: "/login",
  register: "/register",
  verify: "/verify",
  profile: "/profile",
  admin: {
    dashboard: "/admin/dashboard",
    cities: "/admin/cities",
    buses: "/admin/buses",
    trips: "/admin/trips",
    stops: "/admin/stops",
    users: "/admin/users",
    tripNew: "/admin/trips/new",
    tripEdit: (id: string) => `/admin/trips/${id}/edit` as const,
  },
} as const;
