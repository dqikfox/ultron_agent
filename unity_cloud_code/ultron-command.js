// ULTRON Command Execution via Cloud Code
module.exports = async ({ params, context, logger }) => {
  const { command, userId } = params;
  
  logger.info(`User ${userId} executing: ${command}`);
  
  // Rate limiting check
  const rateLimitKey = `rate_limit_${userId}`;
  const count = await context.gameData.get(rateLimitKey) || 0;
  
  if (count > 10) {
    return { error: "Rate limit exceeded", retryAfter: 60 };
  }
  
  await context.gameData.set(rateLimitKey, count + 1, { ttl: 60 });
  
  // Execute command (integrate with ULTRON backend)
  return {
    success: true,
    command: command,
    response: `ULTRON processing: ${command}`,
    timestamp: Date.now()
  };
};
