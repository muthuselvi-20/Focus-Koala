import React from "react";
import { KoalaMood } from "../types";

interface KoalaMascotProps {
  mood: KoalaMood;
  size?: number;
  className?: string;
}

export const KoalaMascot: React.FC<KoalaMascotProps> = ({ mood, size = 120, className = "" }) => {
  return (
    <div
      className={`relative inline-flex items-center justify-center select-none ${className}`}
      style={{ width: size, height: size }}
    >
      <svg
        viewBox="0 0 200 200"
        width={size}
        height={size}
        className="drop-shadow-md transition-transform duration-300 hover:scale-105"
      >
        <defs>
          <radialGradient id={`koalaFur-${mood}`} cx="45%" cy="40%" r="60%">
            <stop
              offset="0%"
              stopColor={
                mood === "happy"
                  ? "#ABC0CE"
                  : mood === "warning"
                  ? "#A5B0B8"
                  : mood === "intervention"
                  ? "#A5B0B8"
                  : "#A0AAB2"
              }
            />
            <stop
              offset="100%"
              stopColor={
                mood === "happy"
                  ? "#73828E"
                  : mood === "intervention"
                  ? "#606A72"
                  : "#707A82"
              }
            />
          </radialGradient>
          <radialGradient id={`innerEar-${mood}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={mood === "happy" ? "#FFD1D1" : "#F2C2C2"} />
            <stop offset="100%" stopColor={mood === "happy" ? "#E5A6A6" : "#D69A9A"} />
          </radialGradient>
        </defs>

        {/* Ears */}
        <circle
          cx="50"
          cy={mood === "disappointed" ? 65 : 55}
          r={mood === "disappointed" ? 30 : 32}
          fill="#8E99A0"
        />
        <circle
          cx="50"
          cy={mood === "disappointed" ? 65 : 55}
          r={mood === "disappointed" ? 18 : 20}
          fill={`url(#innerEar-${mood})`}
        />

        <circle
          cx="150"
          cy={mood === "disappointed" ? 65 : 55}
          r={mood === "disappointed" ? 30 : 32}
          fill="#8E99A0"
        />
        <circle
          cx="150"
          cy={mood === "disappointed" ? 65 : 55}
          r={mood === "disappointed" ? 18 : 20}
          fill={`url(#innerEar-${mood})`}
        />

        {/* Warning Indicator on ear if warning */}
        {mood === "warning" && (
          <g>
            <circle cx="165" cy="35" r="16" fill="#F59E0B" stroke="#FFF" strokeWidth="2.5" />
            <text x="165" y="42" fontSize="18" fontWeight="900" fill="#FFF" textAnchor="middle">
              !
            </text>
          </g>
        )}

        {/* Head */}
        <circle
          cx="100"
          cy={mood === "disappointed" ? 110 : 105}
          r={mood === "disappointed" ? 60 : 62}
          fill={`url(#koalaFur-${mood})`}
        />

        {/* Cheek Fluff */}
        <ellipse cx="44" cy="115" rx="14" ry="10" fill="#B0B9C0" />
        <ellipse cx="156" cy="115" rx="14" ry="10" fill="#B0B9C0" />

        {/* Happy Rosy Cheeks */}
        {mood === "happy" && (
          <>
            <circle cx="56" cy="120" r="12" fill="#F87171" opacity="0.35" />
            <circle cx="144" cy="120" r="12" fill="#F87171" opacity="0.35" />
            <polygon points="175,80 177,84 182,86 177,88 175,93 173,88 168,86 173,84" fill="#FBBF24" />
            <polygon points="25,80 27,84 32,86 27,88 25,93 23,88 18,86 23,84" fill="#FBBF24" />
          </>
        )}

        {/* Eyebrows */}
        {mood === "warning" && (
          <>
            <path d="M 66 78 Q 78 72 88 78" fill="none" stroke="#24272D" strokeWidth="3.5" strokeLinecap="round" />
            <path d="M 112 78 Q 122 72 134 78" fill="none" stroke="#24272D" strokeWidth="3.5" strokeLinecap="round" />
          </>
        )}
        {mood === "intervention" && (
          <>
            <path d="M 68 80 L 86 86" stroke="#24272D" strokeWidth="4.5" strokeLinecap="round" />
            <path d="M 132 80 L 114 86" stroke="#24272D" strokeWidth="4.5" strokeLinecap="round" />
          </>
        )}
        {mood === "disappointed" && (
          <>
            <line x1="68" y1="84" x2="88" y2="86" stroke="#24272D" strokeWidth="4" strokeLinecap="round" />
            <line x1="112" y1="86" x2="132" y2="84" stroke="#24272D" strokeWidth="4" strokeLinecap="round" />
          </>
        )}

        {/* Eyes */}
        {mood === "happy" ? (
          <>
            <path d="M 68 96 Q 76 84 84 96" fill="none" stroke="#24272D" strokeWidth="4.5" strokeLinecap="round" />
            <path d="M 116 96 Q 124 84 132 96" fill="none" stroke="#24272D" strokeWidth="4.5" strokeLinecap="round" />
          </>
        ) : mood === "disappointed" ? (
          <>
            <ellipse cx="76" cy="98" rx="8" ry="4" fill="#1C1E22" />
            <ellipse cx="124" cy="98" rx="8" ry="4" fill="#1C1E22" />
            <path d="M 148 76 C 148 76 156 86 156 91 C 156 95 152 98 148 98 C 144 98 140 95 140 91 C 140 86 148 76 148 76 Z" fill="#60A5FA" />
          </>
        ) : (
          <>
            <ellipse cx="76" cy="95" rx={mood === "warning" ? 9 : 7} ry={mood === "warning" ? 10 : 8} fill="#1C1E22" />
            <circle cx={mood === "intervention" ? 78 : 74} cy={mood === "warning" ? 90 : 92} r={mood === "warning" ? 3.5 : 2.5} fill="#FFFFFF" />
            <ellipse cx="124" cy="95" rx={mood === "warning" ? 9 : 7} ry={mood === "warning" ? 10 : 8} fill="#1C1E22" />
            <circle cx={mood === "intervention" ? 122 : 122} cy={mood === "warning" ? 90 : 92} r={mood === "warning" ? 3.5 : 2.5} fill="#FFFFFF" />
          </>
        )}

        {/* Signature Koala Nose */}
        <ellipse cx="100" cy="112" rx="18" ry="24" fill="#24272D" />
        <ellipse cx="96" cy="104" rx="5" ry="3" fill="#4B525B" />

        {/* Mouth */}
        {mood === "happy" ? (
          <path d="M 86 134 Q 100 152 114 134" fill="#E11D48" stroke="#24272D" strokeWidth="3" strokeLinecap="round" />
        ) : mood === "warning" ? (
          <ellipse cx="100" cy="140" rx="6" ry="7" fill="#24272D" />
        ) : mood === "intervention" ? (
          <line x1="90" y1="140" x2="110" y2="140" stroke="#24272D" strokeWidth="4" strokeLinecap="round" />
        ) : mood === "disappointed" ? (
          <path d="M 88 144 Q 100 138 112 144" fill="none" stroke="#24272D" strokeWidth="3.5" strokeLinecap="round" />
        ) : (
          <path d="M 92 138 Q 100 144 108 138" fill="none" stroke="#24272D" strokeWidth="3.5" strokeLinecap="round" />
        )}

        {/* Pointing Paw for Intervention */}
        {mood === "intervention" && (
          <g transform="translate(136, 110)">
            <circle cx="20" cy="20" r="18" fill="#8E99A0" stroke="#606A72" strokeWidth="2" />
            <ellipse cx="14" cy="10" rx="4" ry="7" fill="#444" transform="rotate(-20 14 10)" />
            <ellipse cx="26" cy="10" rx="4" ry="7" fill="#444" transform="rotate(10 26 10)" />
            <ellipse cx="36" cy="18" rx="4" ry="7" fill="#444" transform="rotate(40 36 18)" />
          </g>
        )}
      </svg>
    </div>
  );
};
