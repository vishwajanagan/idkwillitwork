def fallback_answer(question):
    q=question.lower()
    if 'logp' in q: return '**LogP** estimates how a neutral molecule partitions between octanol and water. Higher values generally indicate greater lipophilicity. RDKit LogP is calculated, not experimental.'
    if 'tpsa' in q or 'polar surface' in q: return '**TPSA** estimates polar surface contributions from polar atoms. It is often used in permeability and absorption screening.'
    if 'smiles' in q: return '**SMILES** encodes a molecular graph as text. Atoms use symbols (`C`, `N`, `O`), branches use parentheses, and ring closures use matching digits. `CCO` represents ethanol.'
    if 'lipinski' in q or 'rule of five' in q: return 'Lipinski screening commonly checks MW ≤500 Da, calculated LogP ≤5, H-bond donors ≤5, and acceptors ≤10. It is not a safety or efficacy test.'
    if '3d' in q or 'conformer' in q: return 'A **3D conformer** is one spatial arrangement of a molecule. Computed conformers are not experimental structures or guaranteed global minima.'
    if 'rotatable' in q: return 'Rotatable bond count approximates flexibility using a toolkit-specific definition; different toolkits may report different counts.'
    return 'Basic fallback mode is active because no AI provider is configured. Ask about SMILES, LogP, TPSA, Lipinski screening, rotatable bonds, or conformers. Set `OPENAI_API_KEY` in deployment secrets for live AI.'
