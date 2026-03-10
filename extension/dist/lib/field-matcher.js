// Field matcher — maps Gemini analysis fields to actual DOM elements
function normalize(s) {
    return s
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, "")
        .replace(/\s+/g, " ")
        .trim();
}
function similarity(a, b) {
    const na = normalize(a);
    const nb = normalize(b);
    if (!na || !nb)
        return 0;
    if (na === nb)
        return 1;
    // Check containment
    if (na.includes(nb) || nb.includes(na))
        return 0.85;
    // Word overlap
    const wordsA = new Set(na.split(" "));
    const wordsB = new Set(nb.split(" "));
    const intersection = new Set([...wordsA].filter((w) => wordsB.has(w)));
    const union = new Set([...wordsA, ...wordsB]);
    if (union.size === 0)
        return 0;
    return intersection.size / union.size;
}
export function matchFields(analysisFields, domFields) {
    const matched = [];
    const usedDomIndices = new Set();
    for (const af of analysisFields) {
        let bestScore = 0;
        let bestIndex = -1;
        for (let i = 0; i < domFields.length; i++) {
            if (usedDomIndices.has(i))
                continue;
            const df = domFields[i];
            // Score against multiple DOM field properties
            const labelScore = similarity(af.field_name, df.label) * 1.0;
            const nameScore = similarity(af.field_name, df.name) * 0.8;
            const idScore = similarity(af.field_name, df.id) * 0.7;
            const placeholderScore = similarity(af.field_name, df.placeholder) * 0.6;
            const score = Math.max(labelScore, nameScore, idScore, placeholderScore);
            if (score > bestScore) {
                bestScore = score;
                bestIndex = i;
            }
        }
        // Accept match if score is reasonable
        if (bestIndex >= 0 && bestScore >= 0.3) {
            usedDomIndices.add(bestIndex);
            matched.push({
                analysis: af,
                domField: domFields[bestIndex],
                domIndex: bestIndex,
                score: bestScore,
            });
        }
    }
    return matched;
}
