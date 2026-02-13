import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { PropsWithChildren } from "react";

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
        <header className="site-header">
          <div className="site-header__inner">
            <Link href="/" className="brand" aria-label="EPL Information Hub Home">
              EPL Hub
            </Link>
            <nav className="gnb" aria-label="Global navigation">
              {NAV_ITEMS.map((item) => {
                if (!item.href) {
                  return (
                    <span key={item.label} className="gnb__item gnb__item--disabled">
                      {item.label}
                    </span>
                  );
                }

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`gnb__item ${isActive(router.pathname, item.href) ? "gnb__item--active" : ""}`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </header>
        <main className="site-main">{children}</main>
      </div>
    </>
  );
}
