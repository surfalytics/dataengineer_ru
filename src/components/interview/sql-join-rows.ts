export const joinTypes = ['LEFT', 'RIGHT', 'FULL', 'INNER', 'CROSS'] as const;
export type JoinType = typeof joinTypes[number];

type Pair = { left: number | null; right: number | null };

// Each pair points to input rows, so two rows with the same id remain distinct.
export function joinPairs(leftKeys: number[], rightKeys: number[], kind: JoinType): Pair[] {
  const pairs: Pair[] = [];
  const matchedRight = new Set<number>();

  for (const [left, key] of leftKeys.entries()) {
    let matched = false;
    for (const [right, otherKey] of rightKeys.entries()) {
      if (kind !== 'CROSS' && key !== otherKey) continue;
      pairs.push({ left, right });
      matchedRight.add(right);
      matched = true;
    }
    if (!matched && (kind === 'LEFT' || kind === 'FULL')) pairs.push({ left, right: null });
  }
  if (kind === 'RIGHT' || kind === 'FULL') {
    rightKeys.forEach((_, right) => {
      if (!matchedRight.has(right)) pairs.push({ left: null, right });
    });
  }
  return pairs;
}
