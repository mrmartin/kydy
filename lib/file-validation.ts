// File validation utilities for image uploads
// Supports validation by extension, MIME type, file content (magic numbers), and size

interface FileValidationResult {
  isValid: boolean;
  error?: string;
  errorCode?: string;
}

// Allowed image extensions - NOTE: SVG is NOT included for security reasons
const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp'] as const;

// Allowed MIME types - NOTE: SVG is NOT included for security reasons
const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png', 
  'image/gif',
  'image/webp'
] as const;

// Magic number signatures for image file types
const IMAGE_SIGNATURES = {
  'image/jpeg': [
    [0xFF, 0xD8, 0xFF], // JPEG
  ],
  'image/png': [
    [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A], // PNG
  ],
  'image/gif': [
    [0x47, 0x49, 0x46, 0x38, 0x37, 0x61], // GIF87a
    [0x47, 0x49, 0x46, 0x38, 0x39, 0x61], // GIF89a
  ],
  'image/webp': [
    // WEBP files start with "RIFF" followed by file size, then "WEBP"
    [0x52, 0x49, 0x46, 0x46], // RIFF (check first 4 bytes, WEBP is at offset 8)
  ]
} as const;

/**
 * Validate file extension
 */
function validateExtension(filename: string): FileValidationResult {
  const extension = filename.split('.').pop()?.toLowerCase();
  
  if (!extension) {
    return {
      isValid: false,
      error: "Soubor nemá příponu",
      errorCode: "NO_EXTENSION"
    };
  }

  if (!ALLOWED_EXTENSIONS.includes(extension as any)) {
    return {
      isValid: false,
      error: `Nepovolená přípona souboru. Povolené: ${ALLOWED_EXTENSIONS.join(', ')}. SVG soubory nejsou povoleny z bezpečnostních důvodů.`,
      errorCode: "INVALID_EXTENSION"
    };
  }

  return { isValid: true };
}

/**
 * Validate MIME type
 */
function validateMimeType(mimeType: string): FileValidationResult {
  if (!ALLOWED_MIME_TYPES.includes(mimeType as any)) {
    return {
      isValid: false,
      error: "Neplatný typ souboru. Nahrajte platný obrázek (JPG, PNG, GIF, WEBP). SVG soubory nejsou povoleny.",
      errorCode: "INVALID_MIME_TYPE"
    };
  }

  return { isValid: true };
}

/**
 * Validate file content by checking magic numbers
 */
function validateFileContent(buffer: Buffer, declaredMimeType: string): FileValidationResult {
  const signatures = IMAGE_SIGNATURES[declaredMimeType as keyof typeof IMAGE_SIGNATURES];
  
  if (!signatures) {
    return {
      isValid: false,
      error: "Nepodporovaný typ obrázku",
      errorCode: "UNSUPPORTED_TYPE"
    };
  }

  // Special handling for WEBP
  if (declaredMimeType === 'image/webp') {
    // Check RIFF header (first 4 bytes)
    const riffSignature = signatures[0];
    if (buffer.length >= 12) {
      const riffMatch = riffSignature.every((byte, index) => buffer[index] === byte);
      // Check WEBP signature at offset 8
      const webpSignature = [0x57, 0x45, 0x42, 0x50]; // "WEBP"
      const webpMatch = webpSignature.every((byte, index) => buffer[8 + index] === byte);
      
      if (riffMatch && webpMatch) {
        return { isValid: true };
      }
    }
  } else {
    // Check if any signature matches
    for (const signature of signatures) {
      if (buffer.length >= signature.length) {
        const matches = signature.every((byte, index) => buffer[index] === byte);
        if (matches) {
          return { isValid: true };
        }
      }
    }
  }

  return {
    isValid: false,
    error: "Obsah souboru neodpovídá deklarovanému typu obrázku. Soubor může být poškozen nebo se jedná o jiný typ souboru.",
    errorCode: "CONTENT_MISMATCH"
  };
}

/**
 * Validate file size (50KB to 10MB)
 */
function validateFileSize(size: number, type: 'poster' | 'avatar' = 'poster'): FileValidationResult {
  const minSize = 50 * 1024; // 50KB
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (size < minSize) {
    return {
      isValid: false,
      error: `Soubor je příliš malý. Minimální velikost je ${Math.round(minSize / 1024)} KB.`,
      errorCode: "FILE_TOO_SMALL"
    };
  }

  if (size > maxSize) {
    return {
      isValid: false,
      error: `Soubor je příliš velký. Maximální velikost je ${Math.round(maxSize / (1024 * 1024))} MB.`,
      errorCode: "FILE_TOO_LARGE"
    };
  }

  return { isValid: true };
}

/**
 * Client-side pre-validation (before upload)
 */
export function validateImageFileClient(file: File): FileValidationResult {
  // 1. Validate extension
  const extensionResult = validateExtension(file.name);
  if (!extensionResult.isValid) {
    return extensionResult;
  }

  // 2. Validate MIME type
  const mimeResult = validateMimeType(file.type);
  if (!mimeResult.isValid) {
    return mimeResult;
  }

  // 3. Validate file size
  const sizeResult = validateFileSize(file.size);
  if (!sizeResult.isValid) {
    return sizeResult;
  }

  return { isValid: true };
}

/**
 * Server-side comprehensive file validation
 */
export async function validateImageFile(
  file: File, 
  buffer: Buffer, 
  type: 'poster' | 'avatar' = 'poster'
): Promise<FileValidationResult> {
  
  // 1. Validate extension
  const extensionResult = validateExtension(file.name);
  if (!extensionResult.isValid) {
    return extensionResult;
  }

  // 2. Validate MIME type
  const mimeResult = validateMimeType(file.type);
  if (!mimeResult.isValid) {
    return mimeResult;
  }

  // 3. Validate file size
  const sizeResult = validateFileSize(file.size, type);
  if (!sizeResult.isValid) {
    return sizeResult;
  }

  // 4. Validate file content (magic numbers)
  const contentResult = validateFileContent(buffer, file.type);
  if (!contentResult.isValid) {
    return contentResult;
  }

  return { isValid: true };
}

/**
 * Get safe filename with validated extension
 */
export function getSafeFilename(originalName: string, userId: string, type: 'poster' | 'avatar' = 'poster'): string {
  const timestamp = Date.now();
  const extension = originalName.split('.').pop()?.toLowerCase() || 'jpg';
  
  // Sanitize the filename
  const prefix = type === 'avatar' ? 'avatar' : 'poster';
  return `${prefix}-${timestamp}-${userId}.${extension}`;
}
