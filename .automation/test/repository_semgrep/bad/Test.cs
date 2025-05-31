using System;
using System.Security.Cryptography;
                    
public class Program
{	
    public void GenerateBadKey() {
        var rng = new System.Random();
        byte[] key = new byte[16];
        rng.NextBytes(key);
        SymmetricAlgorithm cipher = Aes.Create();
        // ruleid: deeptodoruleid: use_weak_rng_for_keygeneration
        cipher.Key = key;
    }
}