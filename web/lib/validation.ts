// Libellé d'une référence publiée en fourchette (page Validation) : les deux bornes ont le même
// libellé au registre, sauf la fin (« borne basse … » / « borne haute … ») ; on garde la partie
// commune jusqu'à la dernière virgule.
export function libelleCommun(basse: string, haute: string): string {
  let n = 0;
  while (n < basse.length && n < haute.length && basse[n] === haute[n]) n++;
  const commun = basse.slice(0, n);
  const virgule = commun.lastIndexOf(", ");
  return virgule > 0 ? commun.slice(0, virgule) : commun;
}
