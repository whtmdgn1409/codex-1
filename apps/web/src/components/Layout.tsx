import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

type NavItem = {
  href?: string;
  label: string;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "홈" },
  { href: "/matches", label: "일정/결과" },
  { href: "/standings", label: "순위표" },
  { href: "/stats", label: "통계" },
  { href: "/teams", label: "구단" },
  { label: "검색" }
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname.startsWith(href);
}

export default function Layout({ children }: PropsWithChildren) {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>EPL Information Hub</title>
        <meta
          name="description"
          content="Premier League unofficial data hub: matches, standings, stats, and teams."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="page-shell">
        <header className="sticky top-0 z-30 border-b border-border/80 bg-white/85 backdrop-blur">
          <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <Link href="/" className="inline-flex items-center gap-2" aria-label="EPL Information Hub Home">
              <span className="rounded-full bg-primary px-2 py-1 text-xs font-semibold text-primary-foreground">EPL</span>
              <span className="text-lg font-black tracking-tight text-primary">Information Hub</span>
            </Link>
            <nav className="flex flex-wrap items-center gap-2" aria-label="Global navigation">
              {NAV_ITEMS.map((item) => {
                if (!item.href) {
                  return (
                    <span
                      key={item.label}
                      className="rounded-full border border-dashed border-border bg-muted/50 px-3 py-1.5 text-sm font-medium text-muted-foreground opacity-70"
                    >
                      {item.label}
                    </span>
                  );
                }

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "rounded-full border px-3 py-1.5 text-sm font-semibold transition-colors",
                      isActive(router.pathname, item.href)
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-border bg-white text-muted-foreground hover:border-primary/40 hover:text-primary"
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
      </div>
    </>
  );
}
