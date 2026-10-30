import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div>
          &copy; {currentYear} DubaiEstate AI 360. All rights reserved.
        </div>
        <div>
          <span>Intern Domain: Full Stack</span> &bull;{' '}
          <span>Branch: <code>feature/week1-fullstack-task-aditya-arora</code></span>
        </div>
      </div>
    </footer>
  );
}
