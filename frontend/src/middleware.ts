import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/', '/login', '/register', '/verify-email', '/reset-password', '/privacy', '/terms'];
const AUTH_PATHS = ['/login', '/register', '/reset-password'];
const PUBLIC_ASSET_PREFIXES = ['/marketing/', '/models/', '/images/', '/fonts/'];
const PUBLIC_FILE_PATTERN = /\.[a-zA-Z0-9]+$/;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasRefreshToken = request.cookies.has('refresh_token');

  if (
    PUBLIC_ASSET_PREFIXES.some((prefix) => pathname.startsWith(prefix)) ||
    PUBLIC_FILE_PATTERN.test(pathname)
  ) {
    return NextResponse.next();
  }

  if (PUBLIC_PATHS.some((p) => pathname === p) || pathname.startsWith('/callback')) {
    if (hasRefreshToken && AUTH_PATHS.some((p) => pathname === p)) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
    return NextResponse.next();
  }

  if (!hasRefreshToken && pathname !== '/') {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|models|images|fonts|marketing|api).*)'],
};
