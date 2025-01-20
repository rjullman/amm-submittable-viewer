import { NextRequest, NextResponse } from 'next/server'

export const config = {
  matcher: ['/(.*)'],
}

export default function middleware(req: NextRequest) {
  console.log("TEST 0")

  const basicAuth = req.headers.get('authorization')
  const url = req.nextUrl

  console.log("TEST 1")

  if (basicAuth) {
    console.log("TEST 2")
    const authValue = basicAuth.split(' ')[1]
    const [user, pwd] = atob(authValue).split(':')
    console.log("TEST 3")

    if (user === '4dmin' && pwd === 'testpwd123') {
      return NextResponse.next()
    }
    console.log("TEST 4")
  }
  url.pathname = '/api/auth'

  console.log("TEST 5")
  return NextResponse.rewrite(url)
}
