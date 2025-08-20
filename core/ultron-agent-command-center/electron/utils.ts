export const is = {
  dev: process.env.NODE_ENV === 'development'
}

export const platform = {
  isWindows: process.platform === 'win32',
  isMacOS: process.platform === 'darwin',
  isLinux: process.platform === 'linux'
}
