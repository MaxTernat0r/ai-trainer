import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const refreshToken = request.cookies.get('refresh_token')?.value;

  if (!refreshToken) {
    return NextResponse.json({ error: 'No refresh token' }, { status: 401 });
  }

  const backendResponse = await fetch(`${BACKEND_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!backendResponse.ok) {
    const response = NextResponse.json({ error: 'Invalid session' }, { status: 401 });
    response.cookies.delete('refresh_token');
    return response;
  }

  const data = await backendResponse.json();
  const response = NextResponse.json({
    accessToken: data.access_token,
    user: data.user,
  });

  // Forward Set-Cookie from backend so refresh token rotation works
  const setCookie = backendResponse.headers.getSetCookie?.();
  if (setCookie) {
    for (const cookie of setCookie) {
      response.headers.append('Set-Cookie', cookie);
    }
  }

  return response;
}
