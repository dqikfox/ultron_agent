module.exports = async ({ params, logger }) => {
  const name = params.name;
  const message = `Hello, ${name}. Welcome to ULTRON Cloud Code!`;
  logger.debug(message);
  return { welcomeMessage: message };
};
