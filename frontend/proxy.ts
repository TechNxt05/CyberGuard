import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)', '/cases(.*)'])
const isDemoCaseRoute = createRouteMatcher(['/dashboard/cases/demo-(.*)'])

export default clerkMiddleware(async (auth, req) => {
    // Landing-page demo cases are public; they only show sample data and never write to the backend.
    const isPublicDemo = isDemoCaseRoute(req) && req.nextUrl.searchParams.get('demo') === 'true'
    if (isProtectedRoute(req) && !isPublicDemo) await auth.protect()
})

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
}
