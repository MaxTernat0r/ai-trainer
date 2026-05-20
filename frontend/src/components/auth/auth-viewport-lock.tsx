'use client';

import { useEffect } from 'react';

function getScrollableAuthContainer(target: EventTarget | null): HTMLElement | null {
  if (!(target instanceof Element)) {
    return null;
  }

  return target.closest<HTMLElement>('[data-auth-form-scroll]');
}

export function AuthViewportLock() {
  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    const scrollY = window.scrollY;
    let touchStartY = 0;

    const previousRootStyle = {
      height: root.style.height,
      overflow: root.style.overflow,
      overscrollBehavior: root.style.overscrollBehavior,
    };
    const previousBodyStyle = {
      height: body.style.height,
      overflow: body.style.overflow,
      overscrollBehavior: body.style.overscrollBehavior,
      position: body.style.position,
      top: body.style.top,
      width: body.style.width,
    };

    root.style.height = '100%';
    root.style.overflow = 'hidden';
    root.style.overscrollBehavior = 'none';
    body.style.height = '100%';
    body.style.overflow = 'hidden';
    body.style.overscrollBehavior = 'none';
    body.style.position = 'fixed';
    body.style.top = `-${scrollY}px`;
    body.style.width = '100%';

    const handleTouchStart = (event: TouchEvent) => {
      touchStartY = event.touches[0]?.clientY ?? 0;
    };

    const handleTouchMove = (event: TouchEvent) => {
      const scroller = getScrollableAuthContainer(event.target);
      if (!scroller) {
        event.preventDefault();
        return;
      }

      const deltaY = (event.touches[0]?.clientY ?? 0) - touchStartY;
      const canScroll = scroller.scrollHeight > scroller.clientHeight;
      const isAtTop = scroller.scrollTop <= 0;
      const isAtBottom = scroller.scrollTop + scroller.clientHeight >= scroller.scrollHeight - 1;

      if (!canScroll || (isAtTop && deltaY > 0) || (isAtBottom && deltaY < 0)) {
        event.preventDefault();
      }
    };

    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      root.style.height = previousRootStyle.height;
      root.style.overflow = previousRootStyle.overflow;
      root.style.overscrollBehavior = previousRootStyle.overscrollBehavior;
      body.style.height = previousBodyStyle.height;
      body.style.overflow = previousBodyStyle.overflow;
      body.style.overscrollBehavior = previousBodyStyle.overscrollBehavior;
      body.style.position = previousBodyStyle.position;
      body.style.top = previousBodyStyle.top;
      body.style.width = previousBodyStyle.width;
      window.scrollTo(0, scrollY);
    };
  }, []);

  return null;
}
