export default function Skeleton({ className = '', style }) {
  return <span aria-hidden="true" className={`block bg-line ${className}`} style={style} />;
}

export function SkeletonRoleRow({ w1 = '60%', w2 = '48%' }) {
  return (
    <div aria-hidden="true" className="flex items-center gap-4 border-b border-line py-[18px]">
      <div className="grid flex-1 gap-[9px]">
        <Skeleton className="h-3.5" style={{ width: w1 }} />
        <Skeleton className="h-2.5" style={{ width: w2 }} />
      </div>
      <span className="size-5 rounded-full border-[1.5px] border-line-2" />
    </div>
  );
}

export function SkeletonBarRow({ w = '44%', tag = 'w-[70px] h-4' }) {
  return (
    <div aria-hidden="true" className="grid gap-2.5">
      <div className="flex justify-between">
        <Skeleton className="h-4" style={{ width: w }} />
        <Skeleton className={tag} />
      </div>
      <Skeleton className="h-1.5" />
    </div>
  );
}
