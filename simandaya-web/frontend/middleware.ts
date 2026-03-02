import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES: Record<string, string> = {
  "/admin": "Admin",
  "/guru": "Guru",
  "/siswa": "Siswa",
};

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const userType = request.cookies.get("user_type")?.value;

  for (const [prefix, requiredRole] of Object.entries(PROTECTED_PREFIXES)) {
    if (path.startsWith(prefix) && userType !== requiredRole) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/guru/:path*", "/siswa/:path*"],
};
